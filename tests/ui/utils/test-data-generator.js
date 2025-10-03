// Test data generator for functional tests
const { faker } = require('@faker-js/faker');

class TestDataGenerator {
  static generateUser(overrides = {}) {
    return {
      username: faker.internet.userName(),
      email: faker.internet.email(),
      password: faker.internet.password({ length: 12, pattern: /[A-Za-z0-9]/, prefix: 'P@' }),
      fullName: faker.person.fullName(),
      ...overrides
    };
  }

  static generateDocumentMetadata(overrides = {}) {
    return {
      title: faker.lorem.words(3) + ' ' + faker.system.commonFileExt(),
      description: faker.lorem.sentence(),
      tags: Array.from({ length: faker.number.int({ min: 1, max: 5 }) }, () => 
        faker.lorem.word()
      ),
      ...overrides
    };
  }

  static generateChatQuery(overrides = {}) {
    const queryTypes = [
      'summarize',
      'extract key points',
      'find similar documents',
      'explain this section',
      'create a table of contents'
    ];
    
    return {
      text: `${faker.helpers.arrayElement(queryTypes)} ${faker.lorem.words(3)}`,
      isComplex: faker.datatype.boolean(),
      ...overrides
    };
  }
}

module.exports = TestDataGenerator;
